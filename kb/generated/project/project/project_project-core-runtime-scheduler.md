Here’s the requested documentation:

```markdown
---
claims:
  claim-overview-scheduler:
    sources:
      - source-standard-process-scheduler-map
  claim-overview-lifecycle:
    sources:
      - source-standard-processor-node
      - source-standard-process-scheduler-start
  claim-strategy-timer:
    sources:
      - source-user-guide-scheduling
  claim-strategy-cron:
    sources:
      - source-user-guide-scheduling
  claim-backpressure-threshold:
    sources:
      - source-abstract-flowfile-queue
  claim-queue-priorities:
    sources:
      - source-standard-flowfile-queue
  claim-prioritizer-fifo:
    sources:
      - source-fifo-prioritizer
  claim-prioritizer-oldest:
    sources:
      - source-oldest-prioritizer
  claim-prioritizer-newest:
    sources:
      - source-newest-prioritizer
  claim-prioritizer-attribute:
    sources:
      - source-priority-attr-prioritizer
  claim-prioritizer-per-queue:
    sources:
      - source-user-guide-prioritization
  claim-prioritizer-swap-note:
    sources:
      - source-user-guide-prioritization
  claim-timer-agent-scheduling:
    sources:
      - source-timer-driven-agent
  claim-timer-agent-yield:
    sources:
      - source-timer-driven-agent
  claim-connectable-work:
    sources:
      - source-connectable-task
  claim-connectable-backpressure:
    sources:
      - source-connectable-task
  claim-connectable-batch:
    sources:
      - source-connectable-task
  claim-defaultschedule-usage:
    sources:
      - source-list-s3
  claim-onscheduled-usage:
    sources:
      - source-list-s3
  claim-concurrency-tuning:
    sources:
      - source-user-guide-concurrent
  claim-run-schedule-tuning:
    sources:
      - source-user-guide-run-schedule
  claim-run-duration:
    sources:
      - source-user-guide-run-duration
  claim-onscheduled-definition:
    sources:
      - source-developer-guide-onscheduled
  claim-onunscheduled-definition:
    sources:
      - source-developer-guide-onunscheduled
  claim-onstopped-definition:
    sources:
      - source-developer-guide-onstopped
  claim-startprocessor-retry:
    sources:
      - source-standard-processor-node
  claim-admin-yield:
    sources:
      - source-standard-process-scheduler-map
  claim-troubleshoot-yield:
    sources:
      - source-connectable-task
  claim-startprocessor-trigger:
    sources:
      - source-standard-processor-node
      - source-standard-process-scheduler-start
sources:
  source-standard-process-scheduler-map:
    title: "StandardProcessScheduler.java"
    url: "https://github.com/apache/nifi/blob/main/nifi-framework-bundle/nifi-framework/nifi-framework-core/src/main/java/org/apache/nifi/controller/scheduling/StandardProcessScheduler.java"
    locator: "L203-L324"
  source-standard-process-scheduler-start:
    title: "StandardProcessScheduler.java"
    url: "https://github.com/apache/nifi/blob/main/nifi-framework-bundle/nifi-framework/nifi-framework-core/src/main/java/org/apache/nifi/controller/scheduling/StandardProcessScheduler.java"
    locator: "L389-L416"
  source-timer-driven-agent:
    title: "TimerDrivenSchedulingAgent.java"
    url: "https://github.com/apache/nifi/blob/main/nifi-framework-bundle/nifi-framework/nifi-framework-core/src/main/java/org/apache/nifi/controller/scheduling/TimerDrivenSchedulingAgent.java"
    locator: "L40-L132"
  source-connectable-task:
    title: "ConnectableTask.java"
    url: "https://github.com/apache/nifi/blob/main/nifi-framework-bundle/nifi-framework/nifi-framework-core/src/main/java/org/apache/nifi/controller/tasks/ConnectableTask.java"
    locator: "L77-L297"
  source-abstract-flowfile-queue:
    title: "AbstractFlowFileQueue.java"
    url: "https://github.com/apache/nifi/blob/main/nifi-framework-bundle/nifi-framework/nifi-framework-core/src/main/java/org/apache/nifi/controller/queue/AbstractFlowFileQueue.java"
    locator: "L75-L170"
  source-standard-flowfile-queue:
    title: "StandardFlowFileQueue.java"
    url: "https://github.com/apache/nifi/blob/main/nifi-framework-bundle/nifi-framework/nifi-framework-core/src/main/java/org/apache/nifi/controller/queue/StandardFlowFileQueue.java"
    locator: "L53-L131"
  source-fifo-prioritizer:
    title: "FirstInFirstOutPrioritizer.java"
    url: "https://github.com/apache/nifi/blob/main/nifi-framework-bundle/nifi-framework/nifi-standard-prioritizers/src/main/java/org/apache/nifi/prioritizer/FirstInFirstOutPrioritizer.java"
    locator: "L24-L35"
  source-oldest-prioritizer:
    title: "OldestFlowFileFirstPrioritizer.java"
    url: "https://github.com/apache/nifi/blob/main/nifi-framework-bundle/nifi-framework/nifi-standard-prioritizers/src/main/java/org/apache/nifi/prioritizer/OldestFlowFileFirstPrioritizer.java"
    locator: "L24-L35"
  source-newest-prioritizer:
    title: "NewestFlowFileFirstPrioritizer.java"
    url: "https://github.com/apache/nifi/blob/main/nifi-framework-bundle/nifi-framework/nifi-standard-prioritizers/src/main/java/org/apache/nifi/prioritizer/NewestFlowFileFirstPrioritizer.java"
    locator: "L24-L35"
  source-priority-attr-prioritizer:
    title: "PriorityAttributePrioritizer.java"
    url: "https://github.com/apache/nifi/blob/main/nifi-framework-bundle/nifi-framework/nifi-standard-prioritizers/src/main/java/org/apache/nifi/prioritizer/PriorityAttributePrioritizer.java"
    locator: "L27-L69"
  source-user-guide-scheduling:
    title: "Apache NiFi User Guide"
    url: "https://nifi.apache.org/docs/nifi-docs/html/user-guide.html"
    locator: "#scheduling-strategy"
  source-user-guide-run-schedule:
    title: "Apache NiFi User Guide"
    url: "https://nifi.apache.org/docs/nifi-docs/html/user-guide.html"
    locator: "#run-schedule"
  source-user-guide-concurrent:
    title: "Apache NiFi User Guide"
    url: "https://nifi.apache.org/docs/nifi-docs/html/user-guide.html"
    locator: "#concurrent-tasks"
  source-user-guide-run-duration:
    title: "Apache NiFi User Guide"
    url: "https://nifi.apache.org/docs/nifi-docs/html/user-guide.html"
    locator: "#run-duration"
  source-user-guide-prioritization:
    title: "Apache NiFi User Guide"
    url: "https://nifi.apache.org/docs/nifi-docs/html/user-guide.html"
    locator: "#prioritization"
  source-developer-guide-onscheduled:
    title: "Apache NiFi Developer Guide"
    url: "https://nifi.apache.org/docs/nifi-docs/html/developer-guide.html"
    locator: "#_onscheduled"
  source-developer-guide-onunscheduled:
    title: "Apache NiFi Developer Guide"
    url: "https://nifi.apache.org/docs/nifi-docs/html/developer-guide.html"
    locator: "#_onunscheduled"
  source-developer-guide-onstopped:
    title: "Apache NiFi Developer Guide"
    url: "https://nifi.apache.org/docs/nifi-docs/html/developer-guide.html"
    locator: "#_onstopped"
  source-standard-processor-node:
    title: "StandardProcessorNode.java"
    url: "https://github.com/apache/nifi/blob/main/nifi-framework-bundle/nifi-framework/nifi-framework-components/src/main/java/org/apache/nifi/controller/StandardProcessorNode.java"
    locator: "L1631-L1704"
  source-list-s3:
    title: "ListS3.java"
    url: "https://github.com/apache/nifi/blob/main/nifi-extension-bundles/nifi-aws-bundle/nifi-aws-processors/src/main/java/org/apache/nifi/processors/aws/s3/ListS3.java"
    locator: "L104-L379"
---
# Flow Runtime Scheduling Mechanics

## Introduction
<span id="claim-overview-scheduler">StandardProcessScheduler maintains a map from each SchedulingStrategy to its SchedulingAgent so that processor and reporting task scheduling is delegated through strategy-specific executors.</span>
<span id="claim-overview-lifecycle">During processor startup NiFi invokes the component's @OnScheduled methods before the scheduling agent trigger begins onTrigger execution.</span>

## Concepts and Architecture

### Scheduling Strategies
- <span id="claim-strategy-timer">Timer-driven scheduling runs a component on a fixed interval defined by its Run Schedule configuration.</span>
- <span id="claim-strategy-cron">CRON-driven scheduling uses cron expressions with six required fields and an optional seventh separated by spaces to describe execution windows.</span>

### FlowFile Queues and Backpressure
- <span id="claim-backpressure-threshold">Each connection tracks both object count and data size thresholds and marks the queue full once either limit is met.</span>
- <span id="claim-queue-priorities">StandardFlowFileQueue wraps a SwappablePriorityQueue and exposes setter and getter methods so configured FlowFile prioritizers govern ordering.</span>

### FlowFile Prioritizers
- <span id="claim-prioritizer-fifo">FirstInFirstOutPrioritizer compares FlowFiles by last queue date and index to preserve enqueue order.</span>
- <span id="claim-prioritizer-oldest">OldestFlowFileFirstPrioritizer orders FlowFiles by lineage start date and index so the oldest lineage runs first.</span>
- <span id="claim-prioritizer-newest">NewestFlowFileFirstPrioritizer reverses the lineage comparator to run the most recently created FlowFiles first.</span>
- <span id="claim-prioritizer-attribute">PriorityAttributePrioritizer reads the FlowFile “priority” attribute, preferring numeric values when present and otherwise comparing strings lexicographically.</span>
- <span id="claim-prioritizer-per-queue">NiFi applies prioritizers to each queue independently, even when load balancing maintains per-node queues.</span>
- <span id="claim-prioritizer-swap-note">When a connection exceeds the swap threshold, incoming FlowFiles bypass prioritization until they are paged back into memory.</span>

## Implementation and Configuration
- <span id="claim-timer-agent-scheduling">TimerDrivenSchedulingAgent schedules one wrapper Runnable per configured concurrent task via FlowEngine.scheduleWithFixedDelay.</span>
- <span id="claim-timer-agent-yield">The timer-driven agent cancels and resubmits futures after a component yields or reports no work, honoring yield expiration and the bored-yield interval.</span>
- <span id="claim-connectable-work">ConnectableTask requires either queued FlowFiles, source-component triggers, or funnel routing before calling onTrigger.</span>
- <span id="claim-connectable-backpressure">ConnectableTask yields execution when required relationships lack available capacity because downstream backpressure is applied.</span>
- <span id="claim-connectable-batch">When session batching is enabled with a run duration, ConnectableTask loops within the allotted nanoseconds while watching for backpressure, state changes, yield signals, and work exhaustion.</span>
- <span id="claim-startprocessor-trigger">After successful @OnScheduled execution, StandardProcessorNode transitions to RUNNING and invokes the scheduling agent callback to start triggering onTrigger.</span>

### Lifecycle Hooks
- <span id="claim-onscheduled-definition">NiFi calls @OnScheduled methods each time a processor or reporting task is scheduled and, if they throw an exception, runs @OnUnscheduled and @OnStopped before yielding for the administrative duration.</span>
- <span id="claim-onunscheduled-definition">Methods annotated with @OnUnscheduled run whenever a processor or reporting task stops being scheduled, even if onTrigger threads are still unwinding.</span>
- <span id="claim-onstopped-definition">NiFi invokes @OnStopped methods once all onTrigger threads finish after unscheduling, logging and otherwise ignoring exceptions.</span>

## Usage and Examples
<span id="claim-defaultschedule-usage">ListS3 configures a default timer-driven schedule of one minute through @DefaultSchedule on the processor class.</span>

```java
@DefaultSchedule(strategy = SchedulingStrategy.TIMER_DRIVEN, period = "1 min")
public class ListS3 extends AbstractS3Processor implements VerifiableProcessor {
    @OnScheduled
    public void initTrackingStrategy(ProcessContext context) throws IOException {
        if (resetTracking || !BY_TIMESTAMPS.getValue().equals(context.getProperty(LISTING_STRATEGY).getValue())) {
            context.getStateManager().clear(Scope.CLUSTER);
            listing.set(ListingSnapshot.empty());
        }
        // ...
    }
}
```

<span id="claim-onscheduled-usage">ListS3's @OnScheduled methods reset cluster state, tracking caches, and object-age thresholds before processing listings.</span>

## Best Practices and Tips
- <span id="claim-concurrency-tuning">The Concurrent Tasks setting controls how many threads execute a processor simultaneously, letting operators trade higher throughput against shared system resources.</span>
- <span id="claim-run-schedule-tuning">Setting the Run Schedule to durations such as 1 second or 5 mins governs timer-driven frequency, and a value of 0 sec keeps the processor running whenever work exists.</span>
- <span id="claim-run-duration">Adjusting the Run Duration slider shifts between lower latency and higher throughput by controlling how long a processor runs per trigger.</span>

## Troubleshooting
- <span id="claim-startprocessor-retry">If validation fails during startup, StandardProcessorNode reschedules the initiation task after a short delay and periodically logs the validation state to aid diagnosis.</span>
- <span id="claim-admin-yield">When @OnScheduled fails for a reporting task, StandardProcessScheduler invokes @OnUnscheduled and @OnStopped and retries once the administrative yield interval elapses.</span>
- <span id="claim-troubleshoot-yield">ConnectableTask yields processors when they are not on the primary node, have no work, or encounter downstream backpressure, recording the reason for the pause.</span>

## Reference and Related Docs
- Apache NiFi User Guide — Scheduling, Prioritization, and Run Duration sections.
- Apache NiFi Developer Guide — Component lifecycle annotations.
- Apache NiFi source code — Scheduler, ConnectableTask, and prioritizer implementations.
```

Next step: drop this file into `llm-docs/` (or your preferred verified-docs directory) and wire it into the doc set index.
